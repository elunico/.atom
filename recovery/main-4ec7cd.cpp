#include <iostream>
#include <random>

class NormalRandomNumbers {
 private:
  std::mt19937 twister;
  std::normal_distribution<double> distro;

 public:
  NormalRandomNumbers(double mean, double stddev) : distro(mean, stddev) {}
  NormalRandomNumbers() : NormalRandomNumbers(17, 3.4) {}

  double operator*() { return distro(twister); }
};

int main(int argc, char const *argv[]) {
  NormalRandomNumbers r{};

  for (int i = 0; i < 10; i++) {
    std::cout << "Random float: " << *r << std::endl;
  }
  return 0;
}
