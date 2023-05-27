# -*- coding: utf-8 -*-
"""leaveoneoutfl.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GIK4HpCxfCe4V1AolfIQAWMUQHGaOq82
"""

!pip install syft==0.2.9

import torch

import helper

from torchvision import datasets

import random
from itertools import permutations
import copy

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms

import syft as sy  # <-- NEW: import the Pysyft library
hook = sy.TorchHook(torch)

#from torchvision import datasets, transforms
#import torchvision.datasets as datasets

def create_workers():
  workers = []
  cartman = sy.VirtualWorker(hook, id = "cartman")
  workers.append(cartman)
  kyle = sy.VirtualWorker(hook, id = "kyle")
  workers.append(kyle)
  kenny = sy.VirtualWorker(hook, id = "kenny")
  workers.append(kenny)
  stan = sy.VirtualWorker(hook, id = "stan")
  workers.append(stan)
  butters = sy.VirtualWorker(hook, id = "butters")
  workers.append(butters)
  wendy = sy.VirtualWorker(hook, id = "wendy")
  workers.append(wendy)
  heidi = sy.VirtualWorker(hook, id = "heidi")
  workers.append(heidi)
  bebe = sy.VirtualWorker(hook, id = "bebe")
  workers.append(bebe)
  nichole = sy.VirtualWorker(hook, id = "nichole")
  workers.append(nichole)
  patty = sy.VirtualWorker(hook, id = "patty")
  workers.append(patty)

  print(workers)
  return workers

def clear_workers(workers):
  for worker in workers:
    worker.clear_objects()

class Arguments():
    def __init__(self):
        self.batch_size = 10 #@param
        self.test_batch_size = 5000 #@param
        self.epochs =  5#@param
        self.lr = 0.15 #@param
        self.momentum = 0.5
        self.no_cuda = False
        self.seed = 1
        self.log_interval = 150 #@param
        self.save_model = False
        self.num_workers = 3  #@param
        self.workers =  [sy.VirtualWorker(hook, id=str(i)) for i in range(self.num_workers)]


args = Arguments()

use_cuda = not args.no_cuda and torch.cuda.is_available()

torch.manual_seed(args.seed)

device = torch.device("cuda" if use_cuda else "cpu")

kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}



federated_train_loader = sy.FederatedDataLoader( # <-- this is now a FederatedDataLoader 
    datasets.MNIST('../data', train=True, download=True,
                   transform=transforms.Compose([
                       transforms.Pad((2,2,2,2)),
                       transforms.ToTensor(),
                       transforms.Normalize((0.1307,), (0.3081,))
                   ]))
    .federate(args.workers), # <-- NEW: we distribute the dataset across all the workers, it's now a FederatedDataset
    # .federate((bob, alice)), # <-- NEW: we distribute the dataset across all the workers, it's now a FederatedDataset
    batch_size=args.batch_size, shuffle=True, **kwargs)

test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=False, transform=transforms.Compose([
                    transforms.Pad((2,2,2,2)),
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                   ])),
    batch_size=args.test_batch_size, shuffle=True, **kwargs)


from collections import defaultdict
worker_counts = defaultdict(int)
worker_data_loader = defaultdict(list)
count = 0
for batch_idx, (data, target) in enumerate(federated_train_loader): # <-- now it is a distributed dataset
    count += 1
    worker_counts[data.location.id] += 1
    worker_data_loader[data.location.id].append((data, target))

class CNN_Net(nn.Module):
    def __init__(self):
        super(CNN_Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, 3, 1)
        self.conv2 = nn.Conv2d(64, 16, 7, 1)
        self.fc1 = nn.Linear(4*4*16, 200)
        self.fc2 = nn.Linear(200, 10)

    def forward(self, x):
        x = x.view(-1, 1, 32, 32)
        x = F.tanh(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.tanh(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4*4*16)
        x = F.tanh(self.fc1(x))
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)
    

class MLP_Net(nn.Module):
    def __init__(self):
        super(MLP_Net, self).__init__()        
        self.fc1 = nn.Linear(1024, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        x = x.view(-1,  1024)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)        
        return F.log_softmax(x, dim=1)

def loadMNISTData():
    federated_train_loader = sy.FederatedDataLoader(
    datasets.MNIST('data', train=True, download=True, transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.1307,), (0.3081,))])).federate((vList[0],vList[1],vList[2],vList[3],vList[4],vList[5],vList[6],vList[7],vList[8],vList[9],vList[10],vList[11],vList[12],vList[13],vList[14],vList[15],vList[16],vList[17],vList[18],vList[19],vList[20],vList[21],vList[22],vList[23],vList[24],vList[25],vList[26],vList[27],vList[28],vList[29],vList[30],vList[31])),batch_size=Arguments.args.batch_size, shuffle=True, **Arguments.kwargs)

    test_loader = torch.utils.data.DataLoader(datasets.MNIST('data', train=False, transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize((0.1307,),(0.3081,))])),batch_size=Arguments.args.test_batch_size, shuffle=True, **Arguments.kwargs)

    return federated_train_loader,test_loader

def train(args, model, device, federated_train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(federated_train_loader): # <-- now it is a distributed dataset
        model.send(data.location) # <-- NEW: send the model to the right location
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        model.get() # <-- NEW: get the model back
        if batch_idx % args.log_interval == 0:
            loss = loss.get() # <-- NEW: get the loss back
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * args.batch_size, len(federated_train_loader) * args.batch_size,
                100. * batch_idx / len(federated_train_loader), loss.item()))

def test(args, model, device, test_loader, verbose=True):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item() # sum up batch loss
            pred = output.argmax(1, keepdim=True) # get the index of the max log-probability 
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    if verbose:
        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
            test_loss, correct, len(test_loader.dataset),
            100. * correct / len(test_loader.dataset)))
    test_acc = 1.* correct / len(test_loader.dataset)
    return test_acc

def averge_parameters(redundant_models):
    final_model = Net().to(device)
    for i, redundant_model in enumerate(redundant_models):
        for param_final, param_redundant in zip(final_model.parameters(), redundant_model.parameters()):
            if i == 0:
                param_final.data = param_redundant.data * 1./ len(redundant_models)
            else:
                param_final.data += param_redundant.data * 1./ len(redundant_models)
    return final_model


def add_update_to_model(model, update, weight=1.0):
    for param_model, param_update in zip(model.parameters(), update):
        param_model.data += weight * param_update.data
    return model

def compute_grad_update(old_model, new_model):
    # maybe later to implement on selected layers/parameters
    return [(new_param.data - old_param.data) for old_param, new_param in zip(old_model.parameters(), new_model.parameters())]


def add_gradient_updates(grad_update_1, grad_update_2):
    assert len(grad_update_1) == len(grad_update_2), "Lengths of the two grad_updates not equal"
    return [ grad_update_1[i] + grad_update_2[i]  for i in range(len(grad_update_1))]

def cosine_similarity(old_grad_update, new_grad_update):    
    cos = nn.CosineSimilarity(dim=0)
    # flatten the gradient updates and find cos_sim layer-wise and then take average
    similarity = 0
    for param_update_old, param_update_new in zip(old_grad_update, new_grad_update):
        similarity += cos(param_update_old.data.view(-1), param_update_new.data.view(-1))
    similarity /= len(old_grad_update) # divide by # layers
    print('similarity',similarity)
    return similarity

def train_shapley(args, model, device, worker_data_loader, optimizer, epoch, contributions, Max_num_sequences=20):
    
    workerIds_str = [worker.id for worker in args.workers]
    workerIds_int = [int(worker.id) for worker in args.workers]

    all_sequences = list(permutations(workerIds_int))
    if len(all_sequences) > Max_num_sequences:
        random.shuffle(all_sequences)
        all_sequences = all_sequences[:Max_num_sequences]

    test_acc_prev_epoch = test(args, model, device, test_loader, verbose=False)

    model_prev_epoch = copy.deepcopy(model)
    model_prev_epoch.load_state_dict(model.state_dict())

    # need to deep clone the model before starting the optimizer step and so on
    # in principle, there should be M different models/different sets of gradient updates after one epoch
    # M being the number of sequences tried

    model.train()
    #  optimization: for each worker, no longer goes through the entire load: 1. random sampling or 2. organized iteration
    grad_updates = [None for _ in workerIds]
    # gather all the model updates
    for workerId in workerIds_str:
        for data, target in worker_data_loader[workerId]:
            model.send(data.location) # <-- NEW: send the model to the right location
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            model.get() # <-- NEW: get the model back
        
        grad_updates[int(workerId)] = compute_grad_update(model_prev_epoch, model)
        model.load_state_dict(model_prev_epoch.state_dict())
    print("decentralized training complete and all the gradient updates collected")
    # compute the running shapley by evaluating using test acc
    update_weight = 1. / len(args.workers)

    marginal_contributions = torch.tensor([0.0 for i in workerIds])
    leave_one_out_contributions = torch.tensor([0.0 for i  in workerIds])
    # coalition_test_acc_dict = {}
    for sequence in all_sequences:
        curr_contributions = []
        sequential_running_model = copy.deepcopy(model_prev_epoch)

        # curr_coalition = set()
        for i, workerId in enumerate(sequence):
            # curr_coalition.add(workerId)
            # coalition = tuple(sorted(list(curr_coalition)))
            # if coalition in coalition_test_acc_dict:
                # test_acc = coalition_test_acc_dict[coalition]
            # else:
                # test_acc = test(args, sequential_running_model, device, test_loader, verbose=False)
                # sequence_test_acc_dict[coalition] = test_acc
            sequential_running_model = add_update_to_model(sequential_running_model, grad_updates[workerId], weight=update_weight)
            test_acc = test(args, sequential_running_model, device, test_loader, verbose=False)
            contribution = test_acc
            if not curr_contributions:
                marginal_contributions[workerId] += contribution - test_acc_prev_epoch
            else:
                marginal_contributions[workerId] += contribution - curr_contributions[-1]
            
                if i == len(sequence)-1 and not leave_one_out_contributions[workerId]:
                    leave_one_out_contributions[workerId] = test_acc - curr_contributions[-1]
            curr_contributions.append(contribution)

        print(curr_contributions)
    num_sequences = len(all_sequences)

    contributions['shapley'] += marginal_contributions/ num_sequences
    contributions['loo'] += leave_one_out_contributions

    print("Marginal contributions this epoch:", marginal_contributions/ num_sequences)
    print("LOO contributions this epoch:", leave_one_out_contributions)

    model.load_state_dict(sequential_running_model.state_dict())

    return contributions

import numpy as np

# try randomly sampling from all the possible sequences
# and compute an approximation to the Shapley values
# for each sequence, there is a contribution value for all workers involved
# and average out all the contribution values for a single worker, across all the sampled sequence to compute this iteration's Shapley Value

workerIds = [worker.id for worker in args.workers]

model = MLP_Net().to(device)
optimizer = optim.SGD(model.parameters(), lr=args.lr) # TODO momentum is not supported at the moment

past_contributions = torch.zeros(np.array(workerIds).shape)
loo_contributions = torch.zeros(np.array(workerIds).shape)
contributions = {'shapley':past_contributions, 'loo':loo_contributions}

for epoch in range(1, args.epochs + 1):
    contributions = train_shapley(args, model, device, worker_data_loader, optimizer, epoch, contributions)
    test(args, model, device, test_loader)
    print(contributions)

if (args.save_model):
    torch.save(model.state_dict(), "mnist_mlp.pt")