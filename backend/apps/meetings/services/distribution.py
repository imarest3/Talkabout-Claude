"""
Service for distributing users into groups for meetings.
"""
from typing import List, Tuple
import math


class UserDistributionService:
    """
    Service to distribute users into groups for videoconferences.

    Ensures:
    - No group exceeds max_participants
    - No group has fewer than min_participants (unless total users < min_participants)
    - Groups are as balanced as possible
    """

    @staticmethod
    def distribute_users(
        user_ids: List[int],
        max_participants: int,
        min_participants: int = 2
    ) -> List[List[int]]:
        """
        Distribute users into balanced groups.

        Args:
            user_ids: List of user IDs to distribute
            max_participants: Maximum number of participants per group
            min_participants: Minimum number of participants per group

        Returns:
            List of groups, where each group is a list of user IDs

        Examples:
            >>> distribute_users([1, 2, 3, 4, 5], max_participants=4, min_participants=2)
            [[1, 2, 3], [4, 5]] # Creates 2 groups of 3 and 2

            >>> distribute_users([1, 2, 3, 4, 5, 6], max_participants=4, min_participants=2)
            [[1, 2, 3], [4, 5, 6]] # Creates 2 groups of 3 each

            >>> distribute_users([1], max_participants=4, min_participants=2)
            [] # Not enough users for a valid group
        """
        total_users = len(user_ids)

        # Edge cases
        if total_users == 0:
            return []

        if total_users < min_participants:
            # Not enough users to form a valid group
            return []

        if total_users <= max_participants:
            # All users fit in one group
            return [user_ids]

        # Calculate optimal number of groups
        num_groups = UserDistributionService._calculate_optimal_groups(
            total_users, max_participants, min_participants
        )

        if num_groups == 0:
            # Cannot create valid distribution
            return []

        # Distribute users as evenly as possible
        groups = []
        users_per_group = total_users // num_groups
        extra_users = total_users % num_groups

        start_idx = 0
        for i in range(num_groups):
            # Distribute extra users to first groups
            group_size = users_per_group + (1 if i < extra_users else 0)
            end_idx = start_idx + group_size
            groups.append(user_ids[start_idx:end_idx])
            start_idx = end_idx

        return groups

    @staticmethod
    def _calculate_optimal_groups(
        total_users: int,
        max_participants: int,
        min_participants: int
    ) -> int:
        """
        Calculate the optimal number of groups.

        Strategy:
        1. Start with minimum number of groups (ceiling of total/max)
        2. Check if distribution would create groups smaller than min
        3. If so, reduce number of groups until all groups meet min requirement

        Returns:
            Number of groups, or 0 if no valid distribution exists
        """
        # Minimum groups needed to not exceed max_participants
        min_groups = math.ceil(total_users / max_participants)

        # Try each possible number of groups starting from minimum
        for num_groups in range(min_groups, 0, -1):
            # Calculate size of smallest group with this distribution
            users_per_group = total_users // num_groups

            # Check if smallest group meets minimum requirement
            if users_per_group >= min_participants:
                # Verify largest group doesn't exceed maximum
                # (largest group gets an extra user if there's a remainder)
                max_group_size = users_per_group + (1 if total_users % num_groups > 0 else 0)

                if max_group_size <= max_participants:
                    return num_groups

        # No valid distribution found
        return 0

    @staticmethod
    def calculate_group_stats(
        total_users: int,
        max_participants: int,
        min_participants: int = 2
    ) -> dict:
        """
        Calculate statistics about how users would be distributed.

        Returns:
            Dictionary with:
                - num_groups: Number of groups
                - users_per_group: List of group sizes
                - is_valid: Whether distribution is possible
        """
        user_ids = list(range(total_users))  # Dummy user IDs
        groups = UserDistributionService.distribute_users(
            user_ids, max_participants, min_participants
        )

        return {
            'num_groups': len(groups),
            'users_per_group': [len(g) for g in groups],
            'is_valid': len(groups) > 0,
            'total_users': total_users
        }
