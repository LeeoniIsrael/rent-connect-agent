"""
Image Analyzer Tool

Description:
Analyzes listing photos for quality and authenticity. Checks image resolution,
detects stock photos, and assesses photo coverage (interior, exterior, amenities).
Lightweight implementation suitable for edge deployment.

Input Streams:
- Image URLs or file paths
- Image metadata (dimensions, format)
- Listing data (for context)

Output Streams:
- Image quality score (0-1)
- Authenticity flags (stock photo detection)
- Coverage assessment (photo types present)
- Quality issues (low resolution, blurry, etc.)

Configuration:
See: config/tools_config.py
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ImageAnalyzerTool:
    """
    Tool for image quality and authenticity analysis.
    
    This is a TOOL (not an agent) - provides image analysis functions
    that agents can use when evaluating listings.
    
    Note: This is a lightweight placeholder. In production, would use
    computer vision models (MobileNet, EfficientNet-Lite) for actual
    image analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize image analyzer tool.
        
        Args:
            config: Configuration with quality thresholds
        """
        self.config = config or {}
        self.min_resolution = self.config.get('min_resolution', 640)  # pixels
        self.min_photo_count = self.config.get('min_photo_count', 3)
        
        logger.info("Image analyzer tool initialized (lightweight mode)")
    
    def analyze_images(
        self,
        listing: Dict
    ) -> Dict[str, Any]:
        """
        Analyze all images for a listing.
        
        Input Stream:
            - listing: Dict with photos list and metadata
        
        Output Stream:
            - Dict with quality_score, authenticity_flags, coverage, issues
        
        Args:
            listing: Listing data with photos
            
        Returns:
            Image analysis results
        """
        listing_id = listing.get('listing_id', 'unknown')
        photos = listing.get('photos', [])
        
        logger.debug(f"Analyzing {len(photos)} images for listing {listing_id}")
        
        if not photos:
            return {
                'listing_id': listing_id,
                'photo_count': 0,
                'quality_score': 0.0,
                'authenticity_flags': ['no_photos'],
                'coverage': {},
                'issues': ['No photos provided']
            }
        
        # Analyze each photo
        photo_analyses = []
        for photo in photos:
            analysis = self._analyze_single_image(photo)
            photo_analyses.append(analysis)
        
        # Aggregate results
        quality_scores = [a['quality_score'] for a in photo_analyses]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Check coverage
        coverage = self._assess_coverage(photo_analyses)
        
        # Collect issues
        all_issues = []
        for analysis in photo_analyses:
            all_issues.extend(analysis.get('issues', []))
        
        # Check for stock photos
        authenticity_flags = []
        stock_photo_count = sum(1 for a in photo_analyses if a.get('is_stock_photo'))
        if stock_photo_count > 0:
            authenticity_flags.append(f'possible_stock_photos: {stock_photo_count}')
        
        # Adjust quality based on photo count
        count_penalty = 0.0
        if len(photos) < self.min_photo_count:
            count_penalty = 0.2
            all_issues.append(f"Too few photos: {len(photos)} (recommended: {self.min_photo_count}+)")
        
        final_quality = max(0.0, avg_quality - count_penalty)
        
        return {
            'listing_id': listing_id,
            'photo_count': len(photos),
            'quality_score': final_quality,
            'authenticity_flags': authenticity_flags,
            'coverage': coverage,
            'issues': list(set(all_issues)),  # Remove duplicates
            'photo_analyses': photo_analyses
        }
    
    def _analyze_single_image(self, photo: Dict) -> Dict[str, Any]:
        """
        Analyze a single photo.
        
        In production, this would:
        - Load image using PIL/OpenCV
        - Run through CNN for quality assessment
        - Check against stock photo database
        - Detect blur, lighting issues, etc.
        
        For now, uses metadata-based heuristics.
        """
        quality_score = 1.0
        issues = []
        
        # Check resolution (if metadata available)
        width = photo.get('width', 1000)
        height = photo.get('height', 800)
        
        if width < self.min_resolution or height < self.min_resolution:
            quality_score -= 0.3
            issues.append(f"Low resolution: {width}x{height}")
        
        # Check file size (proxy for quality)
        file_size_kb = photo.get('file_size_kb', 500)
        if file_size_kb < 50:
            quality_score -= 0.2
            issues.append("Very small file size (possible compression)")
        
        # Detect photo type from filename or URL
        photo_url = photo.get('url', '')
        photo_type = self._detect_photo_type(photo_url)
        
        # Stock photo detection (very basic)
        is_stock_photo = self._is_stock_photo(photo_url)
        if is_stock_photo:
            quality_score -= 0.4
            issues.append("Possible stock photo")
        
        return {
            'url': photo_url,
            'quality_score': max(0.0, quality_score),
            'photo_type': photo_type,
            'is_stock_photo': is_stock_photo,
            'issues': issues
        }
    
    def _detect_photo_type(self, photo_url: str) -> str:
        """
        Detect what the photo shows based on filename/URL.
        
        In production, would use image classification model.
        """
        url_lower = photo_url.lower()
        
        if 'exterior' in url_lower or 'outside' in url_lower or 'front' in url_lower:
            return 'exterior'
        elif 'kitchen' in url_lower:
            return 'kitchen'
        elif 'bedroom' in url_lower or 'bed' in url_lower:
            return 'bedroom'
        elif 'bathroom' in url_lower or 'bath' in url_lower:
            return 'bathroom'
        elif 'living' in url_lower or 'room' in url_lower:
            return 'living_room'
        else:
            return 'unknown'
    
    def _is_stock_photo(self, photo_url: str) -> bool:
        """
        Check if photo is from stock photo site.
        
        In production, would use:
        - Reverse image search
        - Perceptual hashing against stock photo database
        - CNN trained on stock vs. real photos
        """
        stock_domains = [
            'shutterstock', 'istockphoto', 'gettyimages',
            'pexels', 'unsplash', 'pixabay', 'stockphoto'
        ]
        
        url_lower = photo_url.lower()
        return any(domain in url_lower for domain in stock_domains)
    
    def _assess_coverage(self, photo_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Assess what types of photos are covered.
        
        Returns:
            Coverage assessment with photo type counts
        """
        photo_types = [a['photo_type'] for a in photo_analyses]
        
        coverage = {
            'has_exterior': 'exterior' in photo_types,
            'has_kitchen': 'kitchen' in photo_types,
            'has_bedroom': 'bedroom' in photo_types,
            'has_bathroom': 'bathroom' in photo_types,
            'has_living_room': 'living_room' in photo_types,
            'unknown_count': photo_types.count('unknown')
        }
        
        # Calculate coverage score
        required_types = ['exterior', 'kitchen', 'bedroom', 'bathroom']
        coverage_score = sum(1 for t in required_types if t in photo_types) / len(required_types)
        coverage['coverage_score'] = coverage_score
        
        return coverage
    
    def batch_analyze(
        self,
        listings: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze images for multiple listings in batch.
        
        Input Stream:
            - listings: List of listing dictionaries with photos
        
        Output Stream:
            - Dict with analyzed_listings, quality_distribution, issues_summary
        
        Args:
            listings: List of listing data dictionaries
            
        Returns:
            Batch image analysis results
        """
        logger.info(f"Batch analyzing images for {len(listings)} listings")
        
        analyzed_listings = []
        quality_scores = []
        all_issues = []
        
        for listing in listings:
            analysis = self.analyze_images(listing)
            analyzed_listings.append(analysis)
            quality_scores.append(analysis['quality_score'])
            all_issues.extend(analysis['issues'])
        
        # Calculate statistics
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Count issue types
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return {
            'analyzed_listings': analyzed_listings,
            'total_analyzed': len(listings),
            'average_quality_score': avg_quality,
            'quality_distribution': {
                'high': len([s for s in quality_scores if s >= 0.7]),
                'medium': len([s for s in quality_scores if 0.4 <= s < 0.7]),
                'low': len([s for s in quality_scores if s < 0.4])
            },
            'common_issues': sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }


# Singleton instance (tool pattern)
image_analyzer = ImageAnalyzerTool()
