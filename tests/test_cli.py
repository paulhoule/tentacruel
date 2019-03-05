from tentacruel.cli.run import separate_commands

def test_one_command():
    sample =["one","two","three"]
    output = separate_commands(sample)
    assert(len(output)==1)
    assert(output[0] == sample)

def test_two_commands():
    sample =["i","talk","\\","to","the","wind"]
    output = separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])

def test_double_backslash_commands():
    sample =["i","talk","\\\\","to","the","wind"]
    output = separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])

def test_backslash_at_end():
    sample =["i","talk","\\\\","to","the","wind","\\"]
    output = separate_commands(sample)
    assert(len(output)==2)
    assert(output[0] == ["i", "talk"])
    assert(output[1] == ["to", "the", "wind"])


