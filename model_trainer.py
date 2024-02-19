import torch
from tqdm import tqdm
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader

def train(network: torch.nn.Module, test_loader: DataLoader, train_loader: DataLoader, num_epochs: int = 10, lr:float = 0.001, optimizer_type = torch.optim.Adam, loss_function = torch.nn.BCELoss(), plot_loss: bool = False, save_model: bool = False):
    optimizer = optimizer_type(network.parameters(), lr)

    epoch_train_losses = list()
    epoch_test_losses = list()

    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    network.to(device)

    for _ in tqdm(range(num_epochs), total=num_epochs, desc=f"Training in {num_epochs} Epochs"):
        network.train()

        minibatch_training_loss = list()
        minibatch_test_loss = list()
        
        for batch in train_loader:
            network_input, insight_values, targets = batch
            network_input = network_input.to(device)
            targets = targets.to(device)
            
            # Get Model Output (forward pass)
            output = network(network_input)

            # Compute Loss
            loss = loss_function(output, targets)

            # Compute gradients (backward pass)
            loss.backward()  

            # Perform gradient descent update step
            optimizer.step()

            # Reset gradients
            optimizer.zero_grad()

            minibatch_training_loss.append(loss.item())

        epoch_train_losses.append(np.mean(minibatch_training_loss))

        network.eval()

        for batch in test_loader:
            network_input, insight_values, targets = batch

            network_input = network_input.to(device)
            targets = targets.to(device)
            output = network(network_input)
            loss = loss_function(output, targets)
            minibatch_test_loss.append(loss.item())

        epoch_test_losses.append(np.mean(minibatch_test_loss))

    if plot_loss:
        plot_losses(epoch_train_losses, epoch_test_losses)

    if save_model:
        scripted_model = torch.jit.script(network)

        cur_time = datetime.now().strftime("%d-%m-%Y_%H;%M")
        folder_path = fr"{os.getcwd()}\models\{cur_time}"

        os.mkdir(folder_path)
        scripted_model.save(folder_path + r"\model.pt")

        with open(folder_path + r"\metadata.txt", "w") as f:
            f.write(f"DateTime: {cur_time}\n")
            f.write(f"Epochs: {num_epochs}\n")
            f.write(f"Learning Rate: {lr}\n")
            f.write(f"Optimizer: {optimizer_type}\n")
            f.write(f"Loss Function: {loss_function}\n")
            f.write(f"Train Losses: {epoch_train_losses}\n")
            f.write(f"Test Losses: {epoch_test_losses}\n\n")
            f.write(f"Architecture: \n{network}")

    return (epoch_train_losses, epoch_test_losses)

def plot_losses(train_losses: list, test_losses: list):
    plt.title("Model-Loss")
    plt.plot(range(len(train_losses)), train_losses, "orange", range(len(test_losses)), test_losses, "dodgerblue")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend(["Training Loss", "Test Loss"])
    plt.show()