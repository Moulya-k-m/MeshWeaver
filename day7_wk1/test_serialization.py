
from serializer import serialize_call, deserialize_call


# A simple function that we want to send to another node
def multiply(a, b):
    return a * b


print("STEP 1: Creating a function package...")

# Serialize the function and its arguments
encoded = serialize_call(
    multiply,
    args=(10, 20)
)

print("Serialization successful!")
print("Encoded data length:", len(encoded))


print("\nSTEP 2: Reconstructing the function...")

# Deserialize the package
function, args, kwargs = deserialize_call(encoded)

print("Deserialization successful!")


print("\nSTEP 3: Executing the reconstructed function...")

# Execute the reconstructed function
result = function(*args, **kwargs)

print("Execution result:", result)


# Verify the result
assert result == 200, "Test failed!"

print("\nALL TESTS PASSED!")
