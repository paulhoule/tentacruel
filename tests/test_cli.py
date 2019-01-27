from tentacruel.cli.run import Application

def test_one_command():
    cli = Application(None)
    sample =["one","two","three"]
    output = cli.separate_commands(sample)
    assert(len(output)==1)
    assert(output[0] == sample)

def test_two_commands():
    cli = Application(None)
    sample =["i","talk","\\","to","the","wind"]
    output = cli.separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])

def test_double_backslash_commands():
    cli = Application(None)
    sample =["i","talk","\\\\","to","the","wind"]
    output = cli.separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])

def test_backslash_at_end():
    cli = Application(None)
    sample =["i","talk","\\\\","to","the","wind","\\"]
    output = cli.separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])


