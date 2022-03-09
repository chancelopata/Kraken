# Kraken: A hash cracker designed for distributed computing

### Description:

### Technologies utilized:
- Open MPI
- boost.mpi
- C++
### todo/notes

- Crack hashes offline
	- [ ] support bruteforce attack
	- [ ] support dictionary attack using a predefined list (do this first)
	- combination generator
    	- [x] base
    	- [ ] support parallelism
    	- [ ] support distributed computing
- Distributed computing
  - [ ] Support dstributing workload over multiple processes
  - [ ] run on at least 1 linux distro (Ubuntu LTS server)

Stretch Goals
- Support splitting workload over multiple computers with the same operating system.
- run on windows 10
- run on a version of macOS
- Functionality running with split workload on multiple computers with different operating systems