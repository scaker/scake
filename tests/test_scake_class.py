from scake import Scake

def test_init_class_from_lib():
    scake_flow = Scake(config={
        "a": {
            "b": {
                "$collections.OrderedDict": {},
                "myset()": {
                    "__setitem__": ["minh", 100]
                },
                "myget()": {
                    "get": ["minh", 10]
                }
            }
        },
        "c": "/a/b/myget()",
    })
    mycol = scake_flow["/a/b"]
    import collections
    assert isinstance(mycol, collections.OrderedDict)
    scake_flow()
    assert mycol["minh"] == 100
    assert scake_flow["/c"] == 100
    assert scake_flow["/a"]["b"] == scake_flow["/a/b"] # verify the same object
    pass

def test_scake():
    # scake_flow = Scake(module_dir="/home/coder/project/GITHUB/scake/tests/foo", config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)
    scake_flow = Scake(config="/home/coder/project/GITHUB/scake/tests/conf.yml", is_ray=False)

    assert scake_flow["config/bar"] == {"a": 5, "b": 2, "c": 5, "d": 50, "e": 20, "f": 20}
    assert scake_flow["entry/main3"] == 70
    assert scake_flow["entry/main3"] == scake_flow["foo/bar/mysum3()"]
    assert scake_flow["foo/bar/mysum2()"] == 14
    import foo
    assert len(scake_flow["foo"]) == 1
    assert isinstance(scake_flow["foo"]["bar"], foo.bar.Bar)
    assert isinstance(scake_flow["foo/bar"], foo.bar.Bar)
    bar = scake_flow["foo/bar"] # bar object
    assert bar.a == 5 and bar.b == 2
    assert hasattr(bar, "c") and hasattr(bar, "d") and hasattr(bar, "e")
    pass
    
def main():
    test_scake()
    pass

if __name__ == "__main__":
    main()
