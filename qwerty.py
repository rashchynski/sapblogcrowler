import numpy as np

from datetime import datetime

print(
    datetime.strptime('05-08-2024 6:42 PM', "%m-%d-%Y %I:%M %p").strftime("%Y%m%d")
)