import numpy as np
import random

def battle(x,y):
  '''
  plays players x and y against each-other in a round of iterated prisoners dilemma
  return: rewards for x, y
  '''
  # payoffs
  T = 1.5
  R = 1.0
  P = 0.5
  S = 0.0
  # sums
  r_x = 0
  r_y = 0
  # play a number of games
  n_games = 100
  x_prev_play = 0
  y_prev_play = 0
  x.reset()
  y.reset()
  for i in range(n_games):
    x_play = x.play(y_prev_play)
    y_play = y.play(x_prev_play)
    #print "(%d,%d)"%(x_play,y_play)
    if x_play == 1 and y_play == 1:
      r_x += R
      r_y += R
    elif x_play == 1 and y_play == -1:
      r_x += S
      r_y += T
    elif x_play == -1 and y_play == 1:
      r_x += T
      r_y += S
    elif x_play == -1 and y_play == -1:
      r_x += P 
      r_y += P
    else:
      raise Exception("Illegal plays: (%s,%s)"%(str(x_play),str(y_play)))
    x_prev_play = x_play
    y_prev_play = y_play
  # return the total payoffs for each player
  return (r_x,r_y)
 
class SimplePlayer(object):
  def __init__(self,a,b):
    '''
    a = effect coefficient of previous players move (coop = 1, defect = -1)
    b = bias 
    '''
    self._a = a
    self._b = b
  def __str__(self):
    name = ''
    if self._b > 0 and self._a >= self._b:
      name = 't4t'
    elif self._b < 0 and abs(self._a) >= self._b and self._a > 0:
      name = 'nasty-t4t'
    elif self._b > 0 and abs(self._a) < self._b:
      name = 'jesus'
    elif self._b < 0 and abs(self._a) < self._b:
      name = 'lucifer'
    elif self._b > 0 and abs(self._a) > self._b and self._a < 0:
      name = 'nice-reverse'
    elif self._b < 0 and abs(self._a) > self._b and self._a < 0:
      name = 'nasty-reverse'
    else:
      name = '?'
    return "SimplePlayer(a=%1.02f,b=%1.02f) %s"%(self._a,self._b,name)
  def mutate(self):
    return SimplePlayer(
        self._a + np.random.normal()*0.2,
        self._b + np.random.normal()*0.2)
  def reset(self):
    ''' clears state between games '''
    pass
  def play(self,x):
    '''
    x = other players previous move
    return: our move
    allowed to store state between plays
    '''
    activation = self._a*x + self._b
    if activation >= 0:
      return 1
    else:
      return -1

def darwin(pop,battle,n_rounds,mode='full'):
  ''' 
  Parameters:
    pop = population, list of individuals
          each individual has .mutate() that returns a mutated offspring
          and .cross(indiv2) which returns a crossed-over offspring
          and .__str__() that gives brief description for printing
    battle = function of two individuals, returns payoffs for each
    n_rounds = number of rounds to run
    mode = 
      'full': all k^2 pairs played per round, payoffs summed, 
              top 50% survive and reproduce asexually
      'random-dual': k random pairs played per round, payoffs summed,
              top 50% survive and reproduce asexually
  '''
  def print_pop(pop):
    for i in range(len(pop)):
      print "  %03d: %s"%(i,str(pop[i]))
  print "Initial Population:"
  print_pop(pop)
  for round_i in range(n_rounds):
    # generate pairs to play in this round
    if mode == 'full':
      pairs = []
      for x_i in range(len(pop)):
        for y_i in range(len(pop)):
          if x_i != y_i:
            pairs.append((x_i,y_i))
    elif mode == 'random-dual':
      pairs = []
      for i in range(len(pop)):
        # select two different individuals
        x_i = random.randint(0,len(pop)-1)
        while True:
          y_i = random.randint(0,len(pop)-1)
          if y_i != x_i:
            break
        pairs.append((x_i,y_i))
    else:
      raise Exception("Unknown mode '%s'."%mode)
    # play round
    R = np.zeros(len(pop))
    for x_i,y_i in pairs:
      r_x,r_y = battle(pop[x_i],pop[y_i])
      R[x_i] += r_x
      R[y_i] += r_y
    # decimate
    R += np.random.normal(size=len(R))*0.1
    r_med = np.median(R)
    pop2 = []
    survivors = []
    for x_i in range(len(pop)):
      if R[x_i] >= r_med:
        survivors.append(x_i)
    print "r_med: ", r_med
    print "survivors: ", survivors
    print "R: ", R
    for x_i in range(len(pop)):
      if x_i in survivors:
        x2 = pop[x_i]
      else:
        # get offspring of random survivor (with replacement)
        parent_i = random.randint(0,len(survivors)-1)
        x2 = pop[parent_i].mutate()
      pop2.append(x2)
    pop = pop2
    print "Population After %d Rounds:"%(round_i+1)
    print_pop(pop)

if __name__=="__main__":
  pop = []
  for i in range(100):
    pop.append(SimplePlayer(np.random.normal(),np.random.normal()))
  darwin(pop,battle,1000,mode='random-dual')

