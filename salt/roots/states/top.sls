# Author: Joseph Lisee <jlisee@gmail.com>

# Since we are running locally just apply all states to all nodes

base:
  '*':
    - apache
    - haskell
    - gitit