import multiprocessing
import numpy as np
import matplotlib.pyplot as plt

L = 64
SIZES = [64, 128, 256, 512]


def SEND(canal, data):
    canal.put(data)


def RECEIVE(canal):
    return canal.get()


def matmul_module(canal_in, canal_out):
    A, B = RECEIVE(canal_in)
    result = parcs_matmul(A, B)
    SEND(canal_out, result)


def parcs_matmul(A, B):
    n = A.shape[0]

    if n <= L:
        return np.matmul(A, B)

    mid = n // 2
    A00 = A[:mid, :mid];  A01 = A[:mid, mid:]
    A10 = A[mid:, :mid];  A11 = A[mid:, mid:]
    B00 = B[:mid, :mid];  B01 = B[:mid, mid:]
    B10 = B[mid:, :mid];  B11 = B[mid:, mid:]

    pairs = [
        (A00, B00), (A01, B10),
        (A00, B01), (A01, B11),
        (A10, B00), (A11, B10),
        (A10, B01), (A11, B11),
    ]

    canals_to_child   = []
    canals_from_child = []
    procs = []

    for Ai, Bi in pairs:
        q_to   = multiprocessing.Queue()
        q_from = multiprocessing.Queue()
        canals_to_child.append(q_to)
        canals_from_child.append(q_from)
        p = multiprocessing.Process(target=matmul_module, args=(q_to, q_from))
        procs.append(p)
        p.start()
        SEND(q_to, (Ai, Bi))

    partials = [RECEIVE(q) for q in canals_from_child]
    for p in procs:
        p.join()

    C00 = partials[0] + partials[1]
    C01 = partials[2] + partials[3]
    C10 = partials[4] + partials[5]
    C11 = partials[6] + partials[7]

    return np.concatenate(
        [np.concatenate([C00, C01], axis=1),
         np.concatenate([C10, C11], axis=1)],
        axis=0,
    )


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    rng = np.random.default_rng(42)

    errors = {}

    print(f"{'Size':>8}  {'Max error':>12}")
    print("-" * 24)

    for N in SIZES:
        A = rng.random((N, N))
        B = rng.random((N, N))
        C_parcs = parcs_matmul(A, B)
        C_gt    = np.matmul(A, B)
        errors[N] = float(np.max(np.abs(C_parcs - C_gt)))
        print(f"{N:>4}x{N:<4}  {errors[N]:>12.3e}")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([f"{n}×{n}" for n in SIZES], [errors[n] for n in SIZES], color="steelblue")
    ax.set_xlabel("Matrix size")
    ax.set_ylabel("Max absolute error")
    ax.set_title("PARCS vs NumPy: max absolute error (L=64, 1 run per size)")
    ax.set_yscale("log")
    plt.tight_layout()
    plt.savefig("error_bar.png", dpi=150)
    plt.show()