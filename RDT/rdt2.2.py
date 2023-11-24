import random
import time

class SimulatedChannel:
    def __init__(self, loss_rate=0.3):
        self.loss_rate = loss_rate
        self.packet = None

    def send(self, packet):
        if random.random() >= self.loss_rate:
            self.packet = packet
        else:
            self.packet = None

    def receive(self):
        if random.random() >= self.loss_rate:
            return self.packet
        return None


class RDTSender:
    def __init__(self, channel):
        self.channel = channel

    def rdt_send(self, data, receiver):
        packet = self.make_packet(data)
        self.send_packet(packet)
        print("Sending data: ", data, " with sequence number ", packet["seq_num"])
        
        while True:
            ack = receiver.rdt_receive()
            if ack is not None and ack["ack_num"] == packet["seq_num"]:
                print("Received ACK ", ack["ack_num"], ". Transmission successful")
                break
            else:
                print("Timeout occurred. Retransmitting data: ", data)
                self.send_packet(packet)

    def send_packet(self, packet):
        self.channel.send(packet)

    def make_packet(self, data):
        seq_num = random.randint(0, 1)
        return {"seq_num": seq_num, "data": data}


class RDTReceiver:
    def __init__(self, channel):
        self.channel = channel

    def rdt_receive(self):
        packet = self.receive_packet()
        if packet is not None:
            print("Received data: ", packet["data"], " with sequence number ", packet["seq_num"])
            ack_num = packet["seq_num"]
            self.send_acknowledgement(ack_num)
            return {"ack_num": ack_num}
        else:
            print("Transfer unsuccessful")
            return None

    def receive_packet(self):
        return self.channel.receive()

    def send_acknowledgement(self, seq_num):
        ack_packet = {"ack_num": seq_num}
        print("Sending ACK ", ack_packet["ack_num"])
        self.channel.send(ack_packet)


# Example usage:
channel = SimulatedChannel(loss_rate=0.3)
sender = RDTSender(channel)
receiver = RDTReceiver(channel)

file_path = "./test_rdt.txt"  # Replace with the path to your text file

with open(file_path, "r") as file:
    for line in file:
        line = line.strip()
        sender.rdt_send(line, receiver)