from tqdm import tqdm
import torch
from torch.optim import AdamW, SGD,Adam
from torch.utils.data import DataLoader
from dataset import VOCDataset
from model import yolo
from loss import Loss
from torch.autograd import Variable
import numpy as np
import math

init_lr = 0.001
base_lr = 0.01
momentum = 0.9
weight_decay = 5.0e-4
num_epochs = 135
batch_size = 64


def update_lr(optimizer, epoch, burnin_base, burnin_exp=4.0):
	if epoch == 30:
		lr = 0.00005
	elif epoch == 60:
		lr = 0.00001
	else:
		return

	for param_group in optimizer.param_groups:
		param_group['lr'] = lr


def train():
	train_loader = DataLoader(VOCDataset(mode='train'),
							  batch_size=16,
							  num_workers=4,
							  drop_last=True,
							  shuffle=True)
	#net = yolo().cuda()
	net = torch.load('weights/35_net.pk')
	criterion = Loss().cuda()
	optim = SGD(params=net.parameters(),
				lr=0.0001,weight_decay=5e-4,momentum=0.8)
	for epoch in range(100):
		bar = tqdm(train_loader, dynamic_ncols=True)
		batch_loss = []
		bar.set_description_str(f"epoch/{epoch}")
		for i, ele in enumerate(bar):
			update_lr(optim, epoch, float(i) / float(len(train_loader) - 1))
			img, target = ele
			img, target = Variable(img).cuda(), Variable(target).cuda()
			output = net(img)
			optim.zero_grad()
			loss = criterion(output, target.float())
			loss.backward()
			batch_loss.append(loss.item())
			optim.step()
			if i % 5 == 0:
				bar.set_postfix_str(f"loss {np.mean(batch_loss)}")
		if epoch % 5 == 0:
			torch.save(net, f'weights/{epoch}_net.pk')
	torch.save(net, f'weights/{epoch}_net.pk')


def test():
	pass


if __name__ == "__main__":
	train()
