# hello_module.py
def say_hello() -> None:
    print('Hello world!')

def get_name() -> None:
    print(f'当前命名为{__name__}')

if __name__ == '__main__':
    import sys
    for i in sys.path:
        print(i)
    say_hello()
    get_name()

