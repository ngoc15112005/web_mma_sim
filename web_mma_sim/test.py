import random 

def test_defeat_rate(n=1000):
    count_thua = 0
    for _ in range(n):
        a = random.randint(0, 4)
        b = random.randint(0, 4)
        if a == 0 and b == 0:
            count_thua += 1
    print(f"Tổng trận: {n} | Thua: {count_thua} | Tỷ lệ thua: {count_thua / n * 100:.2f}%")

test_defeat_rate()
