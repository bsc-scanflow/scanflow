from multimethod import multimethod
  
  
class GFG(object):
      
    @multimethod
    def double(self, x: int):
        print(2 * x)
  
    @multimethod
    def double(self, x: complex):
        print("sorry, I don't like complex numbers")
          
# Driver Code
obj = GFG()
obj.double(3)
obj.double(6j)