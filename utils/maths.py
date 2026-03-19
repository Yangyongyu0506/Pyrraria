def world_to_screen(
    wx: float, wy: float, camx: float, camy: float
) -> tuple[float, float]:
    """Convert world-space coordinates to screen-space using the camera origin."""
    return wx - camx, wy - camy


def screen_to_world(
    sx: float, sy: float, camx: float, camy: float
) -> tuple[float, float]:
    """Convert screen-space coordinates to world-space using the camera origin."""
    return sx + camx, sy + camy


def center_camera_on(
    target_x: float, target_y: float, screen_w: int, screen_h: int
) -> tuple[int, int]:
    """Return a camera origin that centers the given target on screen."""
    return int(target_x - screen_w // 2), int(target_y - screen_h // 2)
