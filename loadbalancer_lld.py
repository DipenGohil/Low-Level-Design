# -*- coding: utf-8 -*-
"""LoadBalancer_LLD.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16t-Y9FVatKV2XjM5hJHpaOyQ0XQjdPuJ
"""

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_healthy = True
        self.connections = 0  # Initialize connections count

    def is_healthy(self):
        return self.is_healthy

    def set_healthy(self, healthy):
        self.is_healthy = healthy

    def get_server_id(self):
        return self.server_id

    def increment_connections(self):
        self.connections += 1

    def decrement_connections(self):
        if self.connections > 0:
            self.connections -= 1


class LoadBalancingStrategy:
    def get_server(self, servers, request):
        raise NotImplementedError("This method should be overridden.")


class RoundRobinStrategy(LoadBalancingStrategy):
    def __init__(self):
        self.current_index = 0

    def get_server(self, servers, request):
        total_servers = len(servers)
        if total_servers == 0:
            raise Exception("No servers available")
        server = servers[self.current_index]
        self.current_index = (self.current_index + 1) % total_servers
        return server


class LeastConnectionsStrategy(LoadBalancingStrategy):
    def get_server(self, servers, request):
        min_connections = float('inf')
        selected_server = None

        for server in servers:
            if server.is_healthy:
                connections = self.get_connections(server)
                if connections < min_connections:
                    min_connections = connections
                    selected_server = server

        if selected_server is None:
            raise Exception("No healthy servers available")
        selected_server.increment_connections()  # Increment connections count
        return selected_server

    def get_connections(self, server):
        return server.connections


class LoadBalancer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoadBalancer, cls).__new__(cls)
            cls._instance.servers = []
            cls._instance.strategy = None
        return cls._instance

    def add_server(self, server):
        self.servers.append(server)

    def remove_server(self, server):
        self.servers.remove(server)

    def get_server(self, request):
        return self.strategy.get_server(self.servers, request)

    def set_load_balancing_strategy(self, strategy):
        self.strategy = strategy

    def close_connection(self, server):
        server.decrement_connections()  # Decrement connections count


class Request:
    def __init__(self, request_id, data=None):
        """
        Initialize a new request.
        :param request_id: A unique identifier for the request.
        :param data: Optional data associated with the request.
        """
        self.request_id = request_id
        self.data = data

    def get_request_id(self):
        """Return the unique identifier of the request."""
        return self.request_id

    def get_data(self):
        """Return the data associated with the request."""
        return self.data


if __name__ == "__main__":
    # Create servers
    server1 = Server("server1")
    server2 = Server("server2")
    server3 = Server("server3")

    # Create load balancer
    load_balancer = LoadBalancer()
    load_balancer.add_server(server1)
    load_balancer.add_server(server2)
    load_balancer.add_server(server3)

    # Set load balancing strategy
    least_connections_strategy = LeastConnectionsStrategy()
    load_balancer.set_load_balancing_strategy(least_connections_strategy)

    # Create requests
    requests = [Request(f"request{i+1}") for i in range(10)]

    # Dictionary to track which server each request was sent to
    request_server_mapping = {}

    # Distribute requests and print results
    print("Distributing requests to servers:")
    for request in requests:
        selected_server = load_balancer.get_server(request)
        request_server_mapping[request.get_request_id()] = selected_server.get_server_id()
        print(f"{request.get_request_id()} -> {selected_server.get_server_id()}")

    # Remove a server (simulate failure or maintenance)
    print("\nRemoving server2...")
    load_balancer.remove_server(server2)

    # Redistribute requests after removing server2
    print("\nRedistributing requests after removing server2:")
    for request in requests:
        try:
            selected_server = load_balancer.get_server(request)
            request_server_mapping[request.get_request_id()] = selected_server.get_server_id()
            print(f"{request.get_request_id()} -> {selected_server.get_server_id()}")
        except Exception as e:
            print(f"{request.get_request_id()} -> Could not assign to a server: {str(e)}")

    # Print final mapping
    print("\nFinal request-to-server mapping:")
    for request_id, server_id in request_server_mapping.items():
        print(f"{request_id}: {server_id}")
