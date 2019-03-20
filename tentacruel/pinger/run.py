"""
Pinger application.  Periodically poll hosts to see if they are up.  Log state in the
document database,  but report state changes to the message Q

"""
from asyncio import run
from tentacruel.pinger import ensure_proactor, Pinger

if __name__ == "__main__":
    ensure_proactor()
    # pylint: disable=invalid-name
    pinger = Pinger()
    run(pinger.ping_all())
