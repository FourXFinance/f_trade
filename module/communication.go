
package main

import (
	zmq "github.com/pebbe/zmq4"
	"fmt"
)
// The idea would now be to take this module and send emails to the registered users if shit is not going well.
func main() {
	//  Socket to talk to server
	fmt.Println("Connecting to hello world server...")
	requester, _ := zmq.NewSocket(zmq.SUB)
	defer requester.Close()
	requester.SetSubscribe("0")
	requester.Connect("tcp://127.0.0.1:11000")

	for {
		reply, _ := requester.Recv(0)
		fmt.Println("Received ", reply)
	}
}