from agent import graph


def run():
    print("=" * 55)
    print("  Vinmec AI — Trợ lý đặt lịch khám")
    print("  Gõ 'quit' để thoát")
    print("=" * 55)

    history = []

    while True:
        user_input = input("\nBạn: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q", "thoát"):
            print("Tạm biệt! Chúc bạn sức khỏe.")
            break

        history.append(("human", user_input))

        result = graph.invoke({"messages": history})
        final = result["messages"][-1]

        print(f"\nVinmec: {final.content}")

        # Cập nhật history với toàn bộ messages mới
        history = [(m.type, m.content) for m in result["messages"]
                   if hasattr(m, "type") and m.type in ("human", "ai")
                   and m.content]


if __name__ == "__main__":
    run()