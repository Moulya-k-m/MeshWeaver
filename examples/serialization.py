import cloudpickle


# Create a normal Python function
def calculate_total():

    numbers = [100, 200, 300, 400]

    return sum(numbers)


# Step 1: Serialize the function
serialized_function = cloudpickle.dumps(calculate_total)

print("Function serialized successfully")

print("Serialized size:", len(serialized_function), "bytes")


# Step 2: Deserialize the function
restored_function = cloudpickle.loads(serialized_function)

print("Function deserialized successfully")


# Step 3: Execute the restored function
result = restored_function()

print("Execution result:", result)