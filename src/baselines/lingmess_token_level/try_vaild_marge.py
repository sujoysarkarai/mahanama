import torch

# Example inputs
batch_size = 1
subtoken_num = 1765

start_valid = torch.randint(0, 2, (batch_size, subtoken_num), dtype=torch.bool)
end_valid = torch.randint(0, 2, (batch_size, subtoken_num), dtype=torch.bool)

# Compute valid_idx using broadcasting
valid_idx = start_valid[:, :, None] & end_valid[:, None, :]

idx = torch.arange(valid_idx.shape[1], device=valid_idx.device)

valid_idx_count = valid_idx.sum().item()
print(f"Number of True values in valid_idx: {valid_idx_count}")
# print(valid_idx)
print(valid_idx.shape[1], subtoken_num)
# Create an index tensor for the lower triangular mask (including diagonal)
lower_triangular_mask = torch.tril(torch.ones((valid_idx.shape[1], valid_idx.shape[1]), dtype=torch.bool), diagonal=0)

# Set lower triangle and diagonal to False in-place
valid_idx[:, lower_triangular_mask] = False

# Print results
# print("Start Valid:\n", start_valid)
# print("End Valid:\n", end_valid)
# print("Valid Index:\n", valid_idx)

# Count number of True values
start_valid_count = start_valid.sum().item()
end_valid_count = end_valid.sum().item()
valid_idx_count = valid_idx.sum().item()

print(f"Number of True values in start_valid: {start_valid_count}")
print(f"Number of True values in end_valid: {end_valid_count}")
print(f"Number of True values in valid_idx: {valid_idx_count}")