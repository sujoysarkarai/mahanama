import torch
import torch.nn as nn
import torch.nn.functional as F

class BinaryMultimentionModel(nn.Module):
    def __init__(self, input_size=3096):
        super(BinaryMultimentionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 1)
        
    def forward(self, men_vector):
        x = F.relu(self.fc1(men_vector))
        x = F.relu(self.fc2(x))
        logit = torch.sigmoid(self.fc3(x))
        return logit

if __name__ == "__main__":
    # Example usage
    model = BinaryMultimentionModel()
    men_vector_list = torch.randn(10, 3096)  # Example input batch of size 10 * 3096
    gold_output_list = torch.randint(0, 2, (10, 1)).float()  # Example output batch

    # Forward pass
    logit = model(men_vector_list)

    # Loss calculation
    criterion = nn.BCELoss()
    loss = criterion(logit, gold_output_list)

    # Backward pass
    loss.backward()

    # For testing
    with torch.no_grad():
        output_list = (model(men_vector_list) > 0.5).float()  # Thresholding to get binary output
    print(output_list)
