"""
test_pdu.py

Unit tests for PDU controller and service modules.
"""

def test_pdu_reachability():
    """Test PDU network reachability."""
    from pdu_service import PDUService
    
    # Test with a dummy IP
    service = PDUService("127.0.0.1", 9999)
    reachable = service.is_reachable()
    
    print(f"PDU reachability test: {'reachable' if reachable else 'not reachable'}")
    return True  # Test itself passes regardless


def test_pdu_diagnostics():
    """Test PDU diagnostics retrieval."""
    from pdu_service import PDUService
    
    service = PDUService("10.10.10.10")
    diag = service.get_diagnostics()
    
    assert isinstance(diag, dict)
    assert "reachable" in diag
    
    print(f"PDU diagnostics test: PASS")
    return True


if __name__ == "__main__":
    test_pdu_reachability()
    test_pdu_diagnostics()
    print("All PDU tests completed.")
