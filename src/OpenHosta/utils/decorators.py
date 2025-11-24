# We decided do avoid decorators as much as possible in OpenHosta core
# as they make debugging and understanding code way more difficult.
# However, this one is useful for end users to easily configure uncertainty handling.

import math
from ..core.uncertainty import safe

def max_uncertainty(threshold:float=None, acceptable_log_uncertainty:float=None):

    if acceptable_log_uncertainty is not None:
        _threshold = math.exp(acceptable_log_uncertainty)
    elif threshold is not None:
        _threshold = threshold
    else:
        print("mx_uncertainty called with no threshold. All answers will be accepted. Use print_last_uncertainty() to see certainty.")
        _threshold = 1
        
    def configuration_decorator(function_pointer):
        
        wrapper_function_pointer = None
        
        def wrapper(*args, **kwargs):

            with safe(acceptable_cumulated_uncertainty=_threshold):            
                # Call the function
                result = function_pointer(*args, **kwargs)

            # The wrapper shall look like an hosta injected function
            setattr(wrapper_function_pointer, "hosta_injected", function_pointer)
            for attr in dir(function_pointer):
                if not attr.startswith("_"):
                    # Report attr to wrapper
                    setattr(wrapper_function_pointer, attr, getattr(function_pointer, attr))

            return result
                            
        # This variable will be used from inside wrapper later on.     
        wrapper_function_pointer = wrapper

        return wrapper
    
    return configuration_decorator