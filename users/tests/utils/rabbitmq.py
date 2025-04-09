from testcontainers.rabbitmq import RabbitMqContainer


class CustomRabbitMqContainer(RabbitMqContainer):

    def get_connection_url(self):
        return f"amqp://{self.username}:{self.password}@{self.get_container_host_ip()}:{self.get_exposed_port(self.port)}"
