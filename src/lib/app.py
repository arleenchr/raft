"""
    Class for manage the data that used in system for each RaftNode
"""

class KVStore: 
    # Attribute

    """
        Data is a dictionary that has <key>:<value> format with <value> is a string.
        Data can be added, updated, and deleted only from public method.
    """
    __data = {}

    # Method
    def ping(self) -> str:
        """
            Dummy message used for check connection with server.

            Returns:
            - str: "PONG".
        """
        # TODO: Implement ping
        pass 

    def get(self, key : str) -> str:
        """
            Get the value of specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - str: value from specified key, "" if key not exist.
        """
        # TODO: Implement get
        pass 
    
    def set(self, key : str, value:str) -> str:
        """
            Set the value of specified key. If key exist, overwrite the value.

            Parameters:
            - key (str): specified key.
            - value (str): value of key.

            Returns:
            - str: "OK".
        """
        # TODO: Implement set
        pass 

    def strln(self, key : str) -> int:
        """
            Get the value length of specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - int: value length of specified key, 0 if key is not exists.
        """
        # TODO: Implement strln 
        pass 

    def delete(self, key : str) -> str:
        """
            Delete entry with specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - str: value from specified key, "" if key not exist.
        """
        # TODO: Implement delete
        pass

    def append(self, key : str, value:str) -> str:
        """
            Append the value of specified key. If key not exist, add key with empty string before appends the value.

            Parameters:
            - key (str): specified key.
            - value (str): value of key.

            Returns:
            - str: "OK".
        """
        # TODO: Implement append
        pass 