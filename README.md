# Disclaimer:
The code provided here is intended for educational purposes only. It is a demonstration of basic networking, socket programming, and keylogging functionality using Python. The code may not be complete, secure, or suitable for use in production environments. It is essential to understand that unauthorized access to computer systems or capturing sensitive information without consent is illegal and unethical. Using this code to perform any malicious or unauthorized activities is strictly prohibited.

Please use this code responsibly and ensure you have proper authorization before deploying any similar functionality in a real-world scenario. The developers and distributors of this code are not responsible for any misuse or damage that may occur due to the use of this code for illicit purposes.

# aRAT - a remote access tool written in python.

Tested on Windows locally and in a VM with bridged network connection. You must change the IP address of the C2 server in the client.py file.

Features:
- [x] Keylogging
- [x] Screenshot
- [x] Remote command execution
- [x] Webcam Picture Taking
- [x] Transfer files to client
- [x] Creds - Get wifi names and passwords

In Development:
- [x] Microphone listening
— Currently only saving microphone stream when client is closed. Real-time microphone streaming is producing static  
- [x] Browser password grabber
— Currently only working for Chrome 
 
To Do: 
- [ ] Desktop streaming
- [ ] Encrypted communications
- [ ] Port scanner
- [ ] Network scanner (ARP, ping, etc)
- [ ] Allow more than just text files to be uploaded to the client
- [ ] Send messages to client via popup
- [ ] File transfer from client to server
