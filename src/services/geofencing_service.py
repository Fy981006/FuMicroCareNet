import json
from typing import Optional
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from arcgis.geometry import Geometry, Point
from src.models.schemas import Location
from src.utils.config import Settings
import logging

logger = logging.getLogger(__name__)

class GeofencingService:
    def __init__(self, settings: Settings, gis: Optional[GIS] = None):
        self.settings = settings
        self.gis = gis or self._create_gis()
        self.service_area = self._get_service_area()

    def _create_gis(self) -> GIS:
        return GIS(self.settings.ARCGIS_PORTAL_URL, api_key=self.settings.ARCGIS_API_KEY)

    def _get_service_area(self) -> Optional[Geometry]:
        try:
            service_area_layer = FeatureLayer(self.settings.SERVICE_AREA_LAYER_URL, self.gis)
            
            query_result = service_area_layer.query(
                where="1=1",
                out_fields="*",
                return_geometry=True,
                geometry_precision=6,
                out_sr=4326  # WGS84 coordinate system
            )
            
            logger.debug(f"Full query result: {json.dumps(query_result.to_dict(), indent=2)}")
            
            if not query_result.features:
                logger.warning("No features found in the service area layer")
                return None
            
            service_area_feature = query_result.features[0]
            if not service_area_feature.geometry:
                raise ValueError("Invalid geometry in the service area feature")
            
            # Create a Geometry object directly from the feature's geometry
            return Geometry(service_area_feature.geometry)
        except Exception as e:
            error_message = f"Error fetching service area: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise

    def is_location_allowed(self, location: Location) -> bool:
        if not self.service_area:
            logger.warning("Service area not initialized or empty")
            return False
        try:
            point = Point({"x": location.longitude, "y": location.latitude, "spatialReference": {"wkid": 4326}})
            return self.service_area.contains(point)
        except Exception as e:
            logger.error(f"Error checking location {location}: {str(e)}", exc_info=True)
            return False