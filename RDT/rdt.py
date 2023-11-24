import socket
import random
import pickle
from multiprocessing import Process

def read_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

class Packet:
    def __init__(self, seq_no, body, packet_type):
        self.seq_no = seq_no
        self.body = body
        self.type = packet_type

    def __str__(self):
        return f"Packet(seq_no={self.seq_no}, body='{self.body}', type='{self.type}')"

def make_packet(s_no, message, ptype):
    packet = Packet(seq_no=s_no, body=message, packet_type=ptype)
    return packet

def sender(message, loss_probability):
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.bind(('127.0.0.1', 12345))
    seq = 0
    for i in range(len(message)):
        packet = make_packet(seq,message[i],"data")
        sender_socket.sendto(pickle.dumps(packet), ('127.0.0.1', 54321))
        print(f"Sender---Sending: {packet}\n")
        while True:
            data, _ = sender_socket.recvfrom(1024)
            ack = pickle.loads(data)
            if(ack.type == "ACK"):
                print("Sender----Received ACK\n")
                seq = 1 - ack.seq_no
                break
            else:
                print("Sender----Received NAK, Resending\n")
                sender_socket.sendto(pickle.dumps(packet), ('127.0.0.1', 54321))
                print(f"Sender---Re-Transmitting: {packet}\n")
        
    sender_socket.close()

def receiver():
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(('127.0.0.1', 54321))

    while True:
        data, addr = receiver_socket.recvfrom(1024)
        packet = pickle.loads(data)

        if random.random() > 0.3:  # Simulate 30% packet loss
            ack = make_packet(packet.seq_no, "", "ACK")
            receiver_socket.sendto(pickle.dumps(ack), addr)
            print(f"Receiver----Received: {packet}\nReceiver----Sending ACK {ack}\n")
        else:
            ack = make_packet(1 - packet.seq_no, "Negative Ack", "NACK")
            receiver_socket.sendto(pickle.dumps(ack), addr)
            print(f"Receiver----Packet lost\nReceiver----Sending NAK {ack}\n")

if __name__ == "__main__":
    file_path = "./test_rdt.txt"  # file path
    message = read_file(file_path)
    loss_probability = 0.3  # Simulating 30% packet loss

    receiver_process = Process(target=receiver)
    sender_process = Process(target=sender, args=(message, loss_probability))

    receiver_process.start()
    sender_process.start()

    receiver_process.join()
    sender_process.join()