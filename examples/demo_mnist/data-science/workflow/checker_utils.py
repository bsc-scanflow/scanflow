import numpy as np
import tensorflow as tf
import pandas as pd
import os

def scale(x):
    img_rows, img_cols = 28, 28
    # x = df.values
    x = x.reshape(x.shape[0], img_rows, img_cols, 1)
    x = x.astype('float32')
    x /= 255

    return x

def get_loss(model, x, x_index, change_score=False):

    x_pred = model.predict(x)
    x = x.reshape(x.shape[0], 28, 28)
    x_pred = x_pred.reshape(x_pred.shape[0], 28, 28)
    E = pd.DataFrame(index=x_index)

    sz = len(x)
    reconstruction_cost = np.array([np.linalg.norm(np.subtract(x[i],x_pred[i])) for i in range(0,sz)])
    score_anomaly = (reconstruction_cost - np.min(reconstruction_cost)) / np.max(reconstruction_cost)
    
    if change_score:
        E['Loss_mae'] = 1 - score_anomaly
    else:
        E['Loss_mae'] = score_anomaly

    return E

def decide_threshold(ddae_model, x_train, x_train_index, 
                      x_test, x_test_index, wanted_anomalies=10):
    
    width = 0.1
    quantile_high = 0.80
    quantile_low = 1.0 - quantile_high
    # if n_anomalies:
    for trials in range(1, 3): # Iterate until 0.6, 0.4
      
      # Use default score_anomaly
        E_train = get_loss(ddae_model, x_train, x_train_index, change_score=False)
        # Define threshold
        THRESHOLD_HIGH = E_train['Loss_mae'].quantile(q=quantile_high)
        THRESHOLD_LOW = E_train['Loss_mae'].quantile(q=quantile_low)
        # Get AE loss on test
        E_test = get_loss(ddae_model, x_test, x_test_index, change_score=False)


        high =  E_test['Loss_mae'] > THRESHOLD_HIGH
        low =  E_test['Loss_mae'] < THRESHOLD_LOW

        # print(high | low)
        E_test['Anomaly'] = high | low

        E_full = pd.concat([E_train, E_test], sort=False)
        # E_full['Threshold2'] = NAIVE_THRESHOLD
        E_full['Threshold_high'] = THRESHOLD_HIGH
        E_full['Threshold_low'] = THRESHOLD_LOW

        n_anomalies = sum(E_test['Anomaly'])
        print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
        if sum(E_test['Anomaly']) >= wanted_anomalies:
        # print(f"Anomalies={n_anomalies}|Wanted={wanted_anomalies}")
            break

        quantile_high = quantile_high - width
        quantile_low = 1.0 - quantile_high

          # print(quantile_high)


    return E_train, E_test, E_full

def get_checker(x_train_, x_test, date=None, 
                epochs=25, model_path='checker.hdf5', wanted_anomalies=10):
    #np.random.seed(RANDOM_STATE_SEED)
    #tf.random.set_seed(RANDOM_STATE_SEED)

    # pdb.set_trace()
    x_train_index = None
    x_test_index = None

    if date is not None:
        range_periods = x_train_.shape[0] + x_test.shape[0]
        concat_indexes = pd.date_range(date, freq="0.1ms",
                                       periods=range_periods)
        x_train_index = concat_indexes[:x_train_.shape[0]]
        x_test_index = concat_indexes[x_train_.shape[0]:]

    x_train_ = scale(np.copy(x_train_))
    x_test = scale(np.copy(x_test))

    # x_train_noisy = add_noise(x_train_)

    if os.path.isfile(model_path):
        print("[+] Loading Checker")
        ddae_model = tf.keras.models.load_model(model_path)
    else:
        print("[+] Training Checker")
        NUM_EPOCHS=epochs

        BATCH_SIZE=128
        # BATCH_SIZE = 32

        ddae_model = deep_denoise_ae()
        ddae_model.compile(optimizer='adadelta',
                           loss='mse')
        ddae_history = ddae_model.fit(x_train_, x_train_ , # x_train_noisy x_train_
                                      batch_size=BATCH_SIZE,
                                      epochs=NUM_EPOCHS,
                                      validation_split=0.1,
                                      #                   validation_data=(X_test_noisy, X_test),
                                      verbose=1)
        ddae_model.save(model_path)

    
    E_train, E_test, E_full  = decide_threshold(ddae_model,
                                                        x_train_, x_train_index,
                                                        x_test, x_test_index,
                                                        wanted_anomalies)


    x_test_df = pd.DataFrame(x_test_index)

    return ddae_model, E_full, E_test, x_test_df
