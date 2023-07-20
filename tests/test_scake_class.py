from scake import Scake

# def test_scake():
#     # scake_flow = Scake(module_dir="/home/coder/project/GITHUB/scake/tests/foo", config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)
#     scake_flow = Scake(config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)
#     scake_flow()

#     assert scake_flow["config.bar"] == {"a": 5, "b": 2, "c": 5, "d": 50, "e": 20}
#     assert scake_flow["entry"]["main"] == 14
#     assert scake_flow["entry"]["main2"] == 27
#     assert scake_flow["entry"]["main3"] == scake_flow["foo.bar.mysum2"]
#     assert scake_flow["entry"] == {
#         "main": 14,
#         "main2": 27,
#         "main3": 14
#     }
#     import foo
#     assert isinstance(scake_flow["foo.bar"], foo.bar.Bar)
#     bar = scake_flow["foo.bar"] # bar object
#     assert bar.a == 5 and bar.b == 2
#     assert hasattr(bar, "c") and hasattr(bar, "d") and hasattr(bar, "e")
#     assert hasattr(bar, "mysum1") and hasattr(bar, "mysum2")
#     assert bar.mysum1 == 70 and bar.mysum2 == 14
#     pass

def test_scake2():
    # scake_flow = Scake(module_dir="/home/coder/project/GITHUB/scake/tests/foo", config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)
    scake_flow = Scake(config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)
    scake_flow("=/foo")
    assert False

def main():
    test_scake()
    pass

if __name__ == "__main__":
    main()
