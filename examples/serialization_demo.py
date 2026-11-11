
import cloudpickle

# Original Python function
def calculate_total(price, quantity):
    return price * quantity


# Step 1: Serialize the function
serialized_function = cloudpickle.dumps(calculate_total)

print("Function serialized successfully!")
print("Serialized data size:", len(serialized_function), "bytes")


# Step 2: Deserialize the function
restored_function = cloudpickle.loads(serialized_function)

print("Function deserialized successfully!")


# Step 3: Execute the restored function
result = restored_function(250, 4)

print("Execution Result:", result)
