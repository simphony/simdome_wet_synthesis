# Example to use PrecFOAM wrapper
import traceback

from osp.wrappers.prec_nmc_wrappers import PrecFluentSession
from osp.core.namespaces import prec_nmc
from osp.core.utils import pretty_print
from osp.core.utils import Cuds2dot


# create a wrapper session and run it
with PrecFluentSession(delete_simulation_files=False) as session:
    wrapper = prec_nmc.PrecNMCWrapper(session=session)

    accuracy_level = prec_nmc.SliderAccuracyLevel(number=6)
    wrapper.add(accuracy_level)

    pressure = prec_nmc.Pressure(value=101325, unit='Pa')
    wrapper.add(pressure)

    rotationalSpeed = prec_nmc.RotationalSpeed(value=-1005, unit='rpm')
    wrapper.add(rotationalSpeed)

    metal_flowRate = prec_nmc.FlowRate(value=2.1977, unit='lit/hr')
    nh3_flowRate = prec_nmc.FlowRate(value=0.2184, unit='lit/hr')
    naoh_flowRate = prec_nmc.FlowRate(value=0.9171, unit='lit/hr')

    metalFeed = prec_nmc.Feed(name='metals')
    nh3Feed = prec_nmc.Feed(name='nh3')
    naohFeed = prec_nmc.Feed(name='naoh')

    metalFeed.add(metal_flowRate, rel=prec_nmc.hasPart)

    nh3Feed.add(nh3_flowRate, rel=prec_nmc.hasPart)

    naohFeed.add(naoh_flowRate, rel=prec_nmc.hasPart)

    wrapper.add(metalFeed)
    wrapper.add(nh3Feed)
    wrapper.add(naohFeed)

    Cuds2dot(wrapper).render()

    compartmentNetwork = prec_nmc.CompartmentNetwork()
    wrapper.add(compartmentNetwork)

    pretty_print(wrapper.get(oclass=prec_nmc.CompartmentNetwork)[0])

    try:
        # run the session
        session.run()

        pretty_print(wrapper.get(oclass=prec_nmc.CompartmentNetwork)[0])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # session._delete_simulation_files = True
