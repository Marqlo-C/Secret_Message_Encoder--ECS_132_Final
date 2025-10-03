import numpy as np

def simulate_run(distribution, m, i_start, B=20, runs=500, lambda_rate=1, uniform_range=(0, 1), encoding_range=(0, 5)):
    overflow_count = 0
    underflow_count = 0

    for _ in range(runs):
        secret_bits = np.random.choice([0, 1], size=m)

        if distribution == "exponential":
            ipds = np.random.exponential(scale=1/lambda_rate, size=3 * m)
            median = np.log(2) / lambda_rate
        elif distribution == "uniform":
            ipds = np.random.uniform(*uniform_range, size=3 * m)
            median = (uniform_range[1] - uniform_range[0]) / 2
        else:
            raise ValueError("Invalid distribution. Choose 'uniform' or 'exponential'.")

        source_times = np.cumsum(ipds)

        delays = [np.random.uniform(encoding_range[0], median) if bit == 0
                  else np.random.uniform(median, encoding_range[1])
                  for bit in secret_bits]

        time = 0
        packet_index = 0
        CB = 0  # current buffer size

        while CB < i_start and packet_index < len(source_times):
            if source_times[packet_index] >= time:
                CB += 1
            packet_index += 1

        if CB < i_start:
            underflow_count += 1
            continue

        for delay in delays:
            time += delay
            while packet_index < len(source_times) and source_times[packet_index] < time:
                CB += 1
                packet_index += 1

            if CB == 0:
                underflow_count += 1
                break

            CB -= 1
            if CB > B:
                overflow_count += 1
                break

    overflow_prob = overflow_count / runs
    underflow_prob = underflow_count / runs
    success_prob = 1 - (overflow_prob + underflow_prob)

    return overflow_prob, underflow_prob, success_prob

if __name__ == "__main__":
    print("Select Inter-Packet Delay Distribution: 'uniform' or 'exponential'")
    dist = input("Distribution: ").strip().lower()
    m = int(input("Secret message length (m): "))
    i = int(input("Initial buffer size (i): "))

    overflow, underflow, success = simulate_run(dist, m, i)

    print(f"\nResults for m={m}, i={i}, distribution='{dist}':")
    print(f"P(Overflow): {overflow:.3f}")
    print(f"P(Underflow): {underflow:.3f}")
    print(f"P(Success): {success:.3f}")
