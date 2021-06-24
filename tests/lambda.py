
#import couler
def job_d(message):
    couler.run_container(
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=[message],
        step_name="D",
    )

print(job_d(message="D"))

if lambda: job_d(message="D") == (lambda: couler.run_container(
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["D"],
        step_name="D",
    )):
    print(True)

#print(couler.dag([lambda: couler.run_container(
#        image="docker/whalesay:latest",
#        command=["cowsay"],
#        args=["d"],
#        step_name="D",
#    ), lambda: couler.run_container(
#        image="docker/whalesay:latest",
#        command=["cowsay"],
#        args=["2"],
#        step_name="E",
#    )]))