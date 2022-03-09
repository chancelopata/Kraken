#include <thread>
#include <iostream>
#include "generateNextCombination.h"

void my_thread_func()
{
    std::cout<<"hello"<<std::endl;
}

int main(int argc, char** argv)
{

    /* parse flags
    for (int i; i < argc; i++)
    {
        ;
    }*/
    // Split work across computers here.
    
    // Start processes here
    /*
    std::thread t1(my_thread_func);
    std::thread t2(my_thread_func);
    std::thread t3(my_thread_func);
    t1.join();
    t2.join();
    t3.join();*/

    generateNextCombination("aaaa");

}