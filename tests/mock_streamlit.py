from unittest.mock import MagicMock
import sys

# Create mock streamlit
mock_st = MagicMock()
mock_st.success = MagicMock()
mock_st.error = MagicMock()
mock_st.warning = MagicMock()
mock_st.info = MagicMock()
mock_st.write = MagicMock()
mock_st.markdown = MagicMock()
mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
mock_st.form = MagicMock()
mock_st.session_state = {}
mock_st.sidebar = MagicMock()
mock_st.set_page_config = MagicMock()

# Mock streamlit components
mock_components = MagicMock()
mock_components.v1 = MagicMock()
mock_components.v1.html = MagicMock()
mock_st.components = mock_components

# Mock drawable canvas
mock_canvas = MagicMock()
mock_canvas.st_canvas = MagicMock()

# Mock the modules
sys.modules['streamlit'] = mock_st
sys.modules['streamlit.components'] = mock_components
sys.modules['streamlit_drawable_canvas'] = mock_canvas