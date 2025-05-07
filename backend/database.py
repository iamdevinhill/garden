import os
import time
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Neo4jDatabase:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "test1234")
        self.driver = None
        self.max_retries = 5
        self.retry_delay = 5  # seconds
        self.last_connection_attempt = None
        self.connection_timeout = 300  # 5 minutes

    def _should_reconnect(self) -> bool:
        """Check if we should attempt to reconnect based on last attempt"""
        if self.last_connection_attempt is None:
            return True
        return (datetime.now() - self.last_connection_attempt).total_seconds() > self.connection_timeout

    def connect(self):
        """Connect to Neo4j with retries"""
        if self.driver is not None and not self._should_reconnect():
            return True

        for attempt in range(self.max_retries):
            try:
                if self.driver is not None:
                    try:
                        self.driver.close()
                    except Exception:
                        pass
                    self.driver = None

                logger.info(f"Attempting to connect to Neo4j (attempt {attempt + 1}/{self.max_retries})")
                self.driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password)
                )
                
                # Test the connection with a simple query
                with self.driver.session() as session:
                    result = session.run("RETURN 1 as num")
                    if result.single()["num"] != 1:
                        raise Exception("Connection test failed")
                
                self.last_connection_attempt = datetime.now()
                logger.info("Successfully connected to Neo4j")
                return True
                
            except (ServiceUnavailable, AuthError) as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                logger.error("Failed to connect to Neo4j after all retries")
                raise
            except Exception as e:
                logger.error(f"Unexpected error connecting to Neo4j: {str(e)}")
                raise

    def close(self):
        """Close the Neo4j connection"""
        if self.driver is not None:
            try:
                self.driver.close()
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {str(e)}")
            finally:
                self.driver = None
                self.last_connection_attempt = None

    def create_interaction(self, user_input: str, llm_response: str):
        """Create a new interaction node in Neo4j"""
        if not self.driver or self._should_reconnect():
            self.connect()

        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    CREATE (i:Interaction {
                        user_input: $user_input,
                        llm_response: $llm_response,
                        timestamp: datetime()
                    })
                    RETURN i
                    """,
                    user_input=user_input,
                    llm_response=llm_response
                )
                return result.single()
        except Exception as e:
            logger.error(f"Error creating interaction: {str(e)}")
            # If we get a connection error, clear the driver to force reconnect on next attempt
            if isinstance(e, (ServiceUnavailable, AuthError)):
                self.close()
            raise

    def get_all_interactions(self):
        """Get all interactions from Neo4j"""
        if not self.driver or self._should_reconnect():
            self.connect()

        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (i:Interaction)
                    RETURN i
                    ORDER BY i.timestamp DESC
                    """
                )
                return [record["i"] for record in result]
        except Exception as e:
            logger.error(f"Error getting interactions: {str(e)}")
            # If we get a connection error, clear the driver to force reconnect on next attempt
            if isinstance(e, (ServiceUnavailable, AuthError)):
                self.close()
            raise

# Create a global instance
db = Neo4jDatabase() 