from enum import Enum

class ExecutionMode(str, Enum):
  LOCAL = "local"
  GRID = "grid"
  BROWSERSTACK = "browserstack"
