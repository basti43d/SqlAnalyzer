
class ColPair:
    def __init__(self, cols1, cols2):
        self.cols1 = cols1
        self.cols2 = cols2
  
    
    def __eq__(self, other):
        if set(self.cols1) == set(other.cols1) and set(self.cols2) == set(other.cols2):
            return True
        if set(self.cols2) == set(other.cols1) and set(self.cols1) == set(other.cols2):
            return True
        return False

    def __str__(self):
        s = ''
        for i in range(0, len(self.cols1)):
            s += str(self.cols1[i])
            s += ' : '
            s += str(self.cols2[i])
            s += '\n'
        return s