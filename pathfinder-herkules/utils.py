def ask_input() -> int:
    """
    Asks the user for a grid size input and returns the value.
    :return: grid_size: int
    """

    try:
        grid_size = int(input("Enter grid size (10 to 100): "))
    except ValueError:
        print("Invalid grid size value, enter a grid size between 10 and 100.")
        ask_input()

    if not 10 <= grid_size <= 100:
        print("Invalid grid size. Using default value of 10.")
        grid_size = 10

    return grid_size

