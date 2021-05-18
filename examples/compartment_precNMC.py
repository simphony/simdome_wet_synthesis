# Example to use compartment wrapper
import traceback

from osp.wrappers.wet_synthesis_wrappers import CompartmentSession
from osp.core.namespaces import wet_synthesis
from osp.core.utils import pretty_print
from osp.core.utils import Cuds2dot


# create a wrapper session and run it
with CompartmentSession(
        engine="fluent", case="precNMC", delete_simulation_files=False,
        end_time=10) as session:
    wrapper = wet_synthesis.WetSynthesisWrapper(session=session)

    accuracy_level = wet_synthesis.SliderAccuracyLevel(number=1)
    wrapper.add(accuracy_level)

    pressure = wet_synthesis.Pressure(value=101325, unit='Pa')
    wrapper.add(pressure)

    rotationalSpeed = wet_synthesis.RotationalSpeed(value=-1005, unit='rpm')
    wrapper.add(rotationalSpeed)

    metal_flowRate = wet_synthesis.FlowRate(value=2.1977, unit='lit/hr')
    nh3_flowRate = wet_synthesis.FlowRate(value=0.2184, unit='lit/hr')
    naoh_flowRate = wet_synthesis.FlowRate(value=0.9171, unit='lit/hr')

    metalFeed = wet_synthesis.Feed(name='metals')
    nh3Feed = wet_synthesis.Feed(name='nh3')
    naohFeed = wet_synthesis.Feed(name='naoh')

    metalFeed.add(metal_flowRate, rel=wet_synthesis.hasPart)

    nh3Feed.add(nh3_flowRate, rel=wet_synthesis.hasPart)

    naohFeed.add(naoh_flowRate, rel=wet_synthesis.hasPart)

    wrapper.add(metalFeed)
    wrapper.add(nh3Feed)
    wrapper.add(naohFeed)

    Cuds2dot(wrapper).render()

    compartmentNetwork = wet_synthesis.CompartmentNetwork()
    wrapper.add(compartmentNetwork)

    pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

    try:
        # run the session
        session.run()

        pretty_print(wrapper.get(oclass=wet_synthesis.CompartmentNetwork)[0])

    except Exception as e:
        print(e)
        traceback.print_exc()
        # session._delete_simulation_files = True
