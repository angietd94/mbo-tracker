# Service for MBO points aggregation and calculations
import logging

def get_user_points(user_id, mbos, mbo_types):
    """
    Aggregates points for a user by MBO type.
    Returns a dict: {type: points}
    """
    try:
        points = {k: 0 for k in mbo_types}
        
        if not mbos:
            logging.info(f"No MBOs found for user {user_id}")
            return points
            
        for mbo in mbos:
            try:
                # Robust checking for MBO attributes
                if not hasattr(mbo, "creator"):
                    continue
                    
                creator = getattr(mbo, "creator", None)
                if not creator:
                    continue
                    
                creator_id = getattr(creator, "id", None)
                if creator_id != user_id:
                    continue
                    
                mbo_type = getattr(mbo, "mbo_type", None)
                if not mbo_type or mbo_type not in points:
                    continue
                    
                mbo_points = getattr(mbo, "points", 0) or 0
                points[mbo_type] += mbo_points
                
            except Exception as e:
                logging.warning(f"Error processing MBO {getattr(mbo, 'id', 'unknown')}: {e}")
                continue
                
        logging.info(f"Calculated points for user {user_id}: {points}")
        return points
        
    except Exception as e:
        logging.error(f"Error in get_user_points for user {user_id}: {e}")
        return {k: 0 for k in mbo_types}

def get_points_summary(user_id, all_mbos, point_rules):
    """
    Returns a summary dict with points, over/under, and widths for each type and total.
    """
    try:
        if not point_rules:
            raise ValueError("Point rules cannot be empty")
            
        mbo_types = list(point_rules.keys())
        points = get_user_points(user_id, all_mbos, mbo_types)
        summary = {}
        
        total_points = sum(points.values())
        max_total = sum([point_rules[t].get('max', 0) for t in mbo_types])
        
        for t in mbo_types:
            rule = point_rules.get(t, {})
            target = rule.get('target', 0)
            max_points = rule.get('max', 0)
            user_points = points.get(t, 0)
            
            summary[t] = {
                'points': user_points,
                'target': target,
                'max': max_points,
                'over': user_points > max_points,
                'width': round((user_points / max_total) * 100) if max_total > 0 else 0
            }
            
        summary['total_points'] = total_points
        summary['max_total'] = max_total
        summary['percent'] = round((total_points / max_total) * 100) if max_total > 0 else 0
        
        logging.info(f"Generated points summary for user {user_id}: {summary}")
        return summary
        
    except Exception as e:
        logging.error(f"Error in get_points_summary for user {user_id}: {e}")
        # Return safe fallback data
        fallback_summary = {}
        for mbo_type in point_rules.keys():
            fallback_summary[mbo_type] = {
                'points': 0,
                'target': point_rules[mbo_type].get('target', 0),
                'max': point_rules[mbo_type].get('max', 0),
                'over': False,
                'width': 0
            }
        fallback_summary['total_points'] = 0
        fallback_summary['max_total'] = sum([point_rules[t].get('max', 0) for t in point_rules.keys()])
        fallback_summary['percent'] = 0
        return fallback_summary