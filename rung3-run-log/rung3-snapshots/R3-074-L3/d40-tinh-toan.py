# Tinh 10 gia tri tong, ghi vao d40-ket-qua.txt
def main():
    ket_qua = []
    a = [3, 7, 12, 5, 9, 20, 4, 15, 8, 11]
    b = [4, 2, 3, 6, 5, 4, 9, 3, 7, 2]
    for i in range(10):
        tong = a[i] + b[i]
        ket_qua.append(f"dong {i+1}: tong = {tong}")
    with open("/home/james/rung3/d40-ket-qua.txt", "w") as f:
        f.write("\n".join(ket_qua) + "\n")
main()
