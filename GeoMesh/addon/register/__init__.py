
def register_addon():

    # Operators
    from ..operator import register_operators
    register_operators()


def unregister_addon():

    # Operators
    from ..operator import unregister_operators
    unregister_operators()