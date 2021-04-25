import torchvision
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as transforms
import random
import numpy as np
import os
from tqdm import tqdm

from torch.utils.data import DataLoader, Dataset
from torch.optim.lr_scheduler import StepLR

class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output
    
def get_model_params():
    params = {
#       'batch_size': 16,
      'batch_size': 64,
      'test_batch_size': 1000,
      'epochs': 1,
      'lr': 1.0,
      'gamma': 0.7,
      'seed': 42,
      'log_interval': 100,
      'save_model': True
  }

    return params

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    
def get_device():
    return 'cuda' if torch.cuda.is_available() else 'cpu'


# Consider x and y
def get_dataloader(x, y, batch_size, transform, kwargs):
    
    class CustomDataset(Dataset):
        
        def __init__(self, x, y, transform=None):

            self.length = x.shape[0]
            self.x_data = x
            # self.x_data = torch.from_numpy(x)
            self.y_data = y
            # self.y_data = torch.from_numpy(y)
            self.transform = transform

        def __getitem__(self, index):
            x_data = self.x_data[index]

            if self.transform:
                x_data = self.transform(x_data)

            return (x_data, self.y_data[index])

        def __len__(self):
            return self.length

    train_dataset = CustomDataset(x, y, transform)
    train_loader = DataLoader(dataset=train_dataset, 
                              batch_size=batch_size, 
                              shuffle=True, **kwargs)
    
    return train_loader

def get_dataloader_x(x, batch_size, transform, kwargs):
    
    class CustomDataset(Dataset):
        
        def __init__(self, x, transform=None):

            self.length = x.shape[0]
            self.x_data = x
            # self.x_data = torch.from_numpy(x)
            # self.y_data = y
            # self.y_data = torch.from_numpy(y)
            self.transform = transform

        def __getitem__(self, index):
            x_data = self.x_data[index]

            if self.transform:
                x_data = self.transform(x_data)

            # return (x_data, self.y_data[index])
            return x_data

        def __len__(self):
            return self.length

    train_dataset = CustomDataset(x, transform)
    train_loader = DataLoader(dataset=train_dataset, 
                              batch_size=batch_size, 
                              shuffle=False, **kwargs)
    
    return train_loader

def predict_model(model, x):
    params = get_model_params()

    model.eval()
    device = get_device()
    
    kwargs = {'num_workers': 1, 'pin_memory': True}

    transform = transforms.Compose([
                            transforms.ToTensor(),
                            transforms.Normalize((0.1307,), (0.3081,))
                        ])

    test_loader = get_dataloader_x(x, params['test_batch_size'],
                                transform, kwargs)
  
    preds = []

    with torch.no_grad():
        for data in test_loader:
            data = data.to(device)
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)

            preds.extend(pred.cpu().detach().numpy().flatten())

    return np.array(preds)

def train_model(params, model, device, train_loader, optimizer, epoch):
    params = get_model_params()
    # torch.manual_seed(params['seed'])
    model.train()
    for batch_idx, (data, target) in enumerate(tqdm(train_loader)):
        target = target.type(torch.LongTensor)
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % params['log_interval'] == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))

def test_model(model, device, test_loader):
    params = get_model_params()
    # torch.manual_seed(params['seed'])
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in tqdm(test_loader):
            target = target.type(torch.LongTensor)
            data, target = data.to(device), target.to(device)
            
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    score = 100. * correct / len(test_loader.dataset)

    return round(score, 5)

def fit_model(x_train, y_train, model_name='mnist_cnn.pt'):

    params = get_model_params()

    device = get_device()
    # torch.manual_seed(params['seed'])
    set_seed(params['seed'])
    kwargs = {'num_workers': 1, 'pin_memory': True}


    transform = transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])
    train_loader = get_dataloader(x_train, y_train, params['batch_size'],
                                transform, kwargs)

#     test_loader = get_dataloader(x_test, y_test, params['test_batch_size'],
#                                 transform, kwargs)

    model = CNN().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=params['lr'])

    scheduler = StepLR(optimizer, step_size=1, gamma=params['gamma'])
    for epoch in range(1, params['epochs'] + 1):
        train_model(params, model, device, train_loader, optimizer, epoch)
#         score = test_model(model, device, test_loader)
        scheduler.step()

    if params['save_model']:
        torch.save(model.state_dict(), model_name)  

    return model#, score

def evaluate(model, x_test, y_test):

    params = get_model_params()

    device = get_device()
    # torch.manual_seed(params['seed'])
    kwargs = {'num_workers': 1, 'pin_memory': True}
    transform = transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])
    test_loader = get_dataloader(x_test, y_test, params['test_batch_size'],
                                transform, kwargs)

    score = test_model(model, device, test_loader)


    return score