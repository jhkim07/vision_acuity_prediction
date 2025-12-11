import json
import numpy as np 
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torch import nn, optim  # 신경망 모델과 최적화 함수
from PIL import Image
from torchvision import transforms 
from torchvision.models import efficientnet_b0  # 사전 학습된 EfficientNet 모델
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score, ConfusionMatrixDisplay


global device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # GPU 사용 가능 여부 확인