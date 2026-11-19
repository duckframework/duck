"""
Speed test for the caching module.
"""
import os
import time
import random
import string
import platform

from duck.utils.caching import InMemoryCache, DynamicFileCache, KeyAsFolderCache


IS_WINDOWS = platform.system() == "Windows"


class CacheSpeedTest:
    """
    This class performs speed test of Cache classes.
    """
    
    instances_classes = [
        InMemoryCache,
        DynamicFileCache,
        KeyAsFolderCache,
    ]

    def __init__(self, repeat: int = 1):
        self.repeat = repeat
        self.key = self.generate_random_string(32)
        self.results = {}  # Store results for comparison

    @staticmethod
    def generate_random_string(length):
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for _ in range(length))

    def create_instance(self, instance_class):
        """
        Create an instance of the cache class. If the cache class requires a cache directory, ensure that the directory exists before creating the instance.
        """

        def ensure_cache_dir_exists(cache_dir):
            """
            Ensure that the cache directory exists. If it doesn't, create it.
            """
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)

        # Set temmp dir root
        tempdir_root = "/tmp" if not IS_WINDOWS else os.environ.get("TEMP", "C:\\Temp")

        if instance_class == InMemoryCache:
            return instance_class()
        
        elif instance_class == DynamicFileCache:
            cache_dir = f"{tempdir_root}/test_dynamic_file_cache"

            # Ensure the cache directory exists before creating the instance
            ensure_cache_dir_exists(cache_dir)

            # Create an instance of DynamicFileCache with the specified cache directory
            return instance_class(cache_dir=cache_dir)
        
        elif instance_class == KeyAsFolderCache:
            cache_dir = f"{tempdir_root}/test_key_as_folder_cache"

            # Ensure the cache directory exists before creating the instance
            ensure_cache_dir_exists(cache_dir)

            # Create an instance of KeyAsFolderCache with the specified cache directory
            return instance_class(cache_dir=cache_dir)
        
        else:
            raise ValueError(f"Unknown cache class: {instance_class}")

    def test_create(self, instance_class):
        """
        Measure the time taken to create an instance of the cache class.
        """
        start = time.time()

        # Perform the creation of the cache instance
        instance = self.create_instance(instance_class)

        # Record time taken to create the instance
        stop = time.time()
        elapse = stop - start

        # Do some cleanup
        instance.close()

        # Return the elapsed time for creating the instance
        return elapse

    def test_set(self, instance_class):
        """
        Measure the time taken to set a value in the cache.
        """
        data = self.generate_random_string(1024)

        # Create an instance of the cache class
        instance = self.create_instance(instance_class)

        # Record the start time before setting the value in the cache
        start = time.time()

        # Set the value in the cache using the generated key and data
        instance.set(self.key, data)

        # Record the stop time after setting the value in the cache
        stop = time.time()

        # Calculate the elapsed time for setting the value in the cache
        elapse = stop - start

        # Do some cleanup by closing the cache instance
        instance.close()

        # Return the elapsed time for setting the value in the cache
        return elapse

    def test_get(self, instance_class):
        """
        Measure the time taken to get a value from the cache.
        """
        instance = self.create_instance(instance_class)

        # Set start time before retrieving the value from the cache
        start = time.time()

        # Retrieve the value from the cache using the generated key
        _ = instance.get(self.key)

        # Set stop time after retrieving the value from the cache
        stop = time.time()

        # Calculate the elapsed time for retrieving the value from the cache
        elapse = stop - start

        # Do some cleanup by closing the cache instance
        instance.close()

        # Return the elapsed time for retrieving the value from the cache
        return elapse

    def test_delete(self, instance_class):
        """
        Measure the time taken to delete a value from the cache.
        """
        instance = self.create_instance(instance_class)

        # Set start time before deleting the value from the cache
        start = time.time()

        # Perform the deletion of the value from the cache using the generated key
        _ = instance.delete(self.key)

        # Set stop time after deleting the value from the cache
        stop = time.time()

        # Calculate the elapsed time for deleting the value from the cache
        elapse = stop - start

        # Do some cleanup by closing the cache instance
        instance.close()

        # Return the elapsed time for deleting the value from the cache
        return elapse

    def test_clear(self, instance_class):
        """
        Measure the time taken to clear all values from the cache.
        """
        instance = self.create_instance(instance_class)

        # Set start time before clearing all values from the cache
        start = time.time()

        # Clear all values from the cache
        _ = instance.clear()

        # Set stop time after clearing all values from the cache
        stop = time.time()

        # Calculate the elapsed time for clearing all values from the cache
        elapse = stop - start

        # Do some cleanup by closing the cache instance
        instance.close()

        # Return the elapsed time for clearing all values from the cache
        return elapse

    def run_test(self, instance_class):
        """
        Run the speed test for a given cache instance and store the results.
        """
        create_t = 0
        set_t = 0
        get_t = 0
        del_t = 0
        clear_t = 0
        
        for i in range(self.repeat):
            create_t += self.test_create(instance_class)
            set_t += self.test_set(instance_class)
            get_t += self.test_get(instance_class)
            del_t += self.test_delete(instance_class)
            clear_t += self.test_clear(instance_class)
            self.key = self.generate_random_string(32)

        # Store results
        self.results[instance_class.__name__] = {
            "create": create_t / self.repeat,
            "set": set_t / self.repeat,
            "get": get_t / self.repeat,
            "delete": del_t / self.repeat,
            "clear": clear_t / self.repeat,
        }

    def execute_all(self):
        """
        Execute all speed tests for each cache instance and print the summary.
        """
        print("Running caching speed tests...")
        
        for instance_class in self.instances_classes:
            self.run_test(instance_class)

        # Print the summary of results and compare performance
        self.print_summary()

        # Compare performance of different cache instances and print the fastest instance for each operation
        self.compare_performance()

    def print_summary(self):
        print("\nOverall Performance Summary:")

        for instance_name, result in self.results.items():
            print(f"\n[{instance_name}]")
            print(
                f"Create  for {self.repeat} item(s): {result['create']} seconds"
            )
            print(
                f"Set     for {self.repeat} item(s): {result['set']} seconds")
            print(
                f"Get     for {self.repeat} item(s): {result['get']} seconds")
            print(
                f"Delete  for {self.repeat} item(s): {result['delete']} seconds"
            )
            print(
                f"Clear   for {self.repeat} item(s): {result['clear']} seconds"
            )

    def compare_performance(self):
        """
        Compare the performance of different cache instances and print the fastest
        instance for each operation.
        """
        fastest_instance = {}

        for operation in ["create", "set", "get", "delete", "clear"]:
            min_time = float("inf")
            fastest = None

            for instance_name, times in self.results.items():
                if times[operation] < min_time:
                    min_time = times[operation]
                    fastest = instance_name

            # Store the fastest instance and its time for the current operation
            fastest_instance[operation] = (fastest, min_time)

        # Print something
        print("\nFastest Instances for Each Operation:")

        for operation, (instance_name, min_time) in fastest_instance.items():
            print(f"{operation.capitalize():<6}: {instance_name} with {min_time:.6f} seconds")


if __name__ == "__main__":
    # Initialize the CacheSpeedTest with a repeat count of 5
    speed_test = CacheSpeedTest(repeat=5)

    # Execute all speed tests and print the summary
    speed_test.execute_all()
