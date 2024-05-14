"""
    Class for manage the data that used in system for each RaftNode
"""

class KVStore: 

    def __init__(self) -> None: 
        # Attribute
        
        """
            Data is a dictionary that has <key>:<value> format with <value> is a string.
            Data can be added, updated, and deleted only from public method.
        """
        self.__data = {}

    # Method
    def ping(self) -> str:
        """
            Dummy message used for check connection with server.

            Returns:
            - str: "PONG".
        """
        # TODO: Implement ping
        return "PONG"

    def get(self, key : str) -> str:
        """
            Get the value of specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - str: value from specified key, "" if key not exist.
        """
        # TODO: Implement get
        return self.__data.get(key, "")
    
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
        self.__data[key] = value
        return "OK"

    def strln(self, key : str) -> int:
        """
            Get the value length of specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - int: value length of specified key, 0 if key is not exists.
        """
        # TODO: Implement strln 
        string = self.get(key)
        return len(string)

    def delete(self, key : str) -> str:
        """
            Delete entry with specified key.

            Parameters:
            - key (str): specified key.

            Returns:
            - str: value from specified key, "" if key not exist.
        """
        # TODO: Implement delete
        return self.__data.pop(key,"")

    def append(self, key : str, value:str) -> str:
        """
            Append the value of specified key. If key not exist, add key with empty string before appends the value.

            Parameters:
            - key (str): specified key.
            - value (str): value of key.

            Returns:
            - str: "OK".
        """
        string = self.get(key)
        # TODO: Implement append
        if (string != ""):
            self.__data[key] = f'{self.__data[key]}{value}'
        else:
            self.__data[key] = "" + value
        return "OK"