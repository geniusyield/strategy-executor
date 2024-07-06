import logging
from typing import ClassVar


class LoggerUtils:
    """
    A utility class for logging standardized messages.

    This class provides static methods for logging formatted warning messages
    and other utility functions related to logging.
    """

    WARNING_MESSAGE: ClassVar[str] = """
========================================================================
                                                                        
                      ⚠️     WARNING!    ⚠️                            
                                                                        
 THIS IS ONLY A PROOF-OF-CONCEPT EXAMPLE STRATEGY IMPLEMENTATION.       
                                                                        
 IT IS ONLY INTENDED AS IMPLEMENTATION REFERENCE FOR TRADING STRATEGIES.
                                                                        
 THIS IMPLEMENTATION IS NOT PRODUCTION-READY.                           
                                                                        
========================================================================
"""

    @staticmethod
    def log_warning(logger: logging.Logger) -> None:
        """
        Log a standardized warning message using the provided logger.

        This method logs a pre-defined warning message to inform users about
        the nature and limitations of the example strategy implementation.

        Args:
            logger (logging.Logger): The logger instance to use for logging the warning.

        Returns:
            None
        """
        for line in LoggerUtils.WARNING_MESSAGE.strip().split('\n'):
            logger.warning(line)
